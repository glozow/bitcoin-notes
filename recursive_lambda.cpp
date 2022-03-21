#include <functional>
#include <iostream>

int main()
{
    std::cout << "Compute fibonacci (inefficiently) by making a lambda recursively call itself.\n";
    std::function<int(int)> fibonacci;
    fibonacci = [fibonacci](int num_terms)-> int {
        if (num_terms == 0) return 0;
        if (num_terms == 1) return 1;
        return fibonacci(num_terms - 1) + fibonacci(num_terms - 2);
    };

    std::cout << "The 10th fibonacci number is " << fibonacci(10) << "\n";
    std::cout << "The 20th fibonacci number is " << fibonacci(20) << "\n";
    std::cout << "The 30th fibonacci number is " << fibonacci(30) << "\n";

    // Doesn't compile because we use fibonacci before auto is deduced.
    // Can't capture fibonacci by reference before auto is deduced.
    /* const auto fibonacci = [&fibonacci](int num_terms)-> int { */
    /*     if (num_terms == 0) return 0; */
    /*     if (num_terms == 1) return 1; */
    /*     return fibonacci(num_terms - 1) + fibonacci(num_terms - 2); */
    /* }; */

    // Okay but you can pass it in as an argument before auto is deduced, right?
    // compiles but throws
    const auto fibonacci2 = [](int num_terms) {
        auto fibonacci_impl = [](int num_terms, auto& self_ref) -> int {
            if (num_terms == 0) return 0;
            if (num_terms == 1) return 1;
            try {
                return self_ref(num_terms - 1, self_ref) + self_ref(num_terms - 2, self_ref);
            } catch(const std::bad_function_call& err) {
                std::cout << err.what() << "\n";
            }
        };
        return fibonacci_impl(num_terms, fibonacci_impl);
    };

    std::cout << "The 10th fibonacci number is " << fibonacci2(10) << "\n";
    std::cout << "The 20th fibonacci number is " << fibonacci2(20) << "\n";
    std::cout << "The 30th fibonacci number is " << fibonacci2(30) << "\n";
    return 0;
}
